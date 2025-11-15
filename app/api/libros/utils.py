import os
def _ejecutar_plan_filesystem(plan):
    """
    Helper para ejecutar el plan de archivos DESPUÉS del commit.
    Primero borra los antiguos, luego renombra los nuevos.
    """
    # 1. Borrar antiguos
    for path_archivo in plan["antiguos_a_borrar"]:
        if os.path.exists(path_archivo):
            try:
                os.remove(path_archivo)
            except Exception as e:
                # ALERTA: La BBDD está actualizada, pero el archivo antiguo 
                # no se pudo borrar. Registrar esto.
                print(f"ALERTA POST-COMMIT: No se pudo borrar el archivo antiguo {path_archivo}: {e}")
                
    # 2. Renombrar nuevos (el "commit" del sistema de archivos)
    for path_temp, path_final in plan["temporales_a_renombrar"]:
        try:
            os.rename(path_temp, path_final)
        except Exception as e:
            # ERROR CRÍTICO: La BBDD apunta al nuevo archivo,
            # pero no pudimos renombrarlo.
            print(f"ERROR CRÍTICO POST-COMMIT: No se pudo renombrar {path_temp} a {path_final}: {e}")

def _limpiar_temporales_en_fallo(plan):
    """
    Helper para borrar los archivos .tmp si el commit de la BBDD falla.
    """
    for path_temp in plan["temporales_a_borrar_en_fallo"]:
        if os.path.exists(path_temp):
            try:
                os.remove(path_temp)
            except Exception as e:
                 print(f"ALERTA ROLLBACK: No se pudo limpiar el temporal {path_temp}: {e}")