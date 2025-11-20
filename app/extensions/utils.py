import boto3
from botocore.config import Config
from boto3.s3.transfer import TransferConfig # <--- IMPORTANTE: Importar esto

class DigitalOceanSpaces:
    def __init__(self, app=None):
        self.client = None
        self.bucket_name = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Cargamos config desde app.config
        self.bucket_name = app.config.get('DO_SPACES_BUCKET')
        
        self.client = boto3.client(
            's3',
            region_name=app.config.get('DO_SPACES_REGION'),
            endpoint_url=app.config.get('DO_SPACES_ENDPOINT'),
            aws_access_key_id=app.config.get('DO_SPACES_KEY'),
            aws_secret_access_key=app.config.get('DO_SPACES_SECRET'),
            # Configuración de conexión (Timeouts y Firma)
            config=Config(signature_version='s3v4', connect_timeout=5, read_timeout=5)
        )

    def upload_file(self, file_or_path, destination_path, content_type=None, acl='private'):
        try:
            # Configuración Turbo: Umbral bajo (1MB) y muchos hilos (10)
            MB = 1024 ** 2
            transfer_config = TransferConfig(
                multipart_threshold=1 * MB,
                max_concurrency=10, 
                multipart_chunksize=1 * MB,
                use_threads=True
            )

            extra_args = {'ACL': acl}
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Lógica Inteligente: ¿Es ruta o es memoria?
            if isinstance(file_or_path, str):
                # ES DISCO: Boto3 optimiza esto al máximo con hilos
                self.client.upload_file(
                    Filename=file_or_path,
                    Bucket=self.bucket_name,
                    Key=destination_path,
                    ExtraArgs=extra_args,
                    Config=transfer_config
                )
            else:
                # ES MEMORIA: Método tradicional
                if hasattr(file_or_path, 'seek'):
                    file_or_path.seek(0)

                self.client.upload_fileobj(
                    file_or_path,
                    self.bucket_name,
                    destination_path,
                    ExtraArgs=extra_args,
                    Config=transfer_config
                )
            return True
        except Exception as e:
            print(f"Error subiendo a Spaces: {e}")
            raise e

    def get_presigned_url(self, file_path, expiration=300):
        """
        Genera una URL temporal para descargar un archivo privado.
        expiration: Tiempo en segundos (300s = 5 minutos).
        """
        try:
            # Generamos la URL firmada
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Error generando URL firmada: {e}")
            return None
    
    def delete_file(self, file_path):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception as e:
            print(f"Error borrando archivo {file_path}: {e}")
            return False