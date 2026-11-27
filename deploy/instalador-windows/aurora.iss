; Instalador de Aurora para Windows (instalación local, un solo PC). Lo compila el workflow
; .github/workflows/instalador-windows.yml con Inno Setup 6:  ISCC /DAppVersion=2.12.0 deploy\instalador-windows\aurora.iss
; Requiere Docker Desktop (el instalador ofrece instalarlo con winget). Solo datos ficticios; IA SIMULADA.

#ifndef AppVersion
  #define AppVersion "2.12.0"
#endif
#define Repo "..\.."

[Setup]
AppId={{A8DA6E37-4F38-4FAA-A782-9D9E1B9FE340}
AppName=Aurora
AppVersion={#AppVersion}
AppVerName=Aurora {#AppVersion}
AppPublisher=Equipo Proyecto Aurora (INACAP)
DefaultDirName={localappdata}\Aurora
DefaultGroupName=Aurora
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#Repo}\dist-instalador
OutputBaseFilename=AuroraSetup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=Aurora {#AppVersion}
LicenseFile=aviso.txt

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "docker-compose.local.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "scripts\*.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "aviso.txt"; DestDir: "{app}"; Flags: ignoreversion
; Código para construir las imágenes en el PC (sin el modelo de IA, sin dependencias ni secretos)
Source: "{#Repo}\backend\*"; DestDir: "{app}\app\backend"; Excludes: "venv\*,.venv\*,__pycache__,*.pyc,.env,.pytest_cache\*,inference_service\*,htmlcov\*,.coverage"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Repo}\src\*"; DestDir: "{app}\app\src"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Repo}\public\*"; DestDir: "{app}\app\public"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Repo}\deploy\Caddyfile"; DestDir: "{app}\app\deploy"; Flags: ignoreversion
Source: "{#Repo}\deploy\.env.example"; DestDir: "{app}\app\deploy"; Flags: ignoreversion
Source: "{#Repo}\Dockerfile"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\.dockerignore"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\package.json"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\package-lock.json"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\index.html"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\vite.config.ts"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\tsconfig*.json"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\postcss.config.js"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\tailwind.config.js"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "{#Repo}\eslint.config.js"; DestDir: "{app}\app"; Flags: ignoreversion

[Icons]
Name: "{group}\Abrir Aurora"; Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File ""{app}\scripts\iniciar.ps1"""; WorkingDir: "{app}"
Name: "{group}\Detener Aurora"; Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\detener.ps1"""; WorkingDir: "{app}"
Name: "{group}\Terminar configuración de Aurora"; Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\configurar.ps1"" -PedirAdmin"; WorkingDir: "{app}"
Name: "{group}\Reparar Aurora"; Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\reparar.ps1"""; WorkingDir: "{app}"
Name: "{group}\Registros de Aurora"; Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\registros.ps1"""; WorkingDir: "{app}"
Name: "{group}\Desinstalar Aurora"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Aurora"; Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File ""{app}\scripts\iniciar.ps1"""; WorkingDir: "{app}"; Tasks: escritorio

[Tasks]
Name: "escritorio"; Description: "Crear un acceso directo en el escritorio"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\configurar.ps1"" -DatosAdmin ""{tmp}\admin.txt"" -Puerto {code:Puerto}"; WorkingDir: "{app}"; StatusMsg: "Construyendo e iniciando Aurora (5 a 15 minutos la primera vez)..."; Check: DockerListo

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\scripts\desinstalar.ps1"" {code:BorrarDatos}"; RunOnceId: "AuroraDown"; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: files; Name: "{app}\.env"

[Code]
var
  AdminPage: TInputQueryWizardPage;
  PuertoPage: TInputQueryWizardPage;
  DockerRecienInstalado: Boolean;

function DockerExe(): String;
begin
  Result := ExpandConstant('{commonpf}\Docker\Docker\resources\bin\docker.exe');
end;

function DockerInstalado(): Boolean;
var Code: Integer;
begin
  Result := FileExists(DockerExe()) or
            (Exec('cmd.exe', '/c where docker', '', SW_HIDE, ewWaitUntilTerminated, Code) and (Code = 0));
end;

function DockerListo(): Boolean;
begin
  Result := not DockerRecienInstalado;
end;

function Puerto(Param: String): String;
begin
  Result := Trim(PuertoPage.Values[0]);
end;

function BorrarDatos(Param: String): String;
begin
  Result := '';
  if MsgBox('¿Borrar también la base de datos y las imágenes de Aurora? Esto no se puede deshacer.',
            mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    Result := '-BorrarDatos';
end;

function InitializeSetup(): Boolean;
var Code: Integer;
begin
  Result := True;
  DockerRecienInstalado := False;
  if not DockerInstalado() then
  begin
    case MsgBox('Aurora necesita Docker Desktop y no está instalado.' + #13#10#13#10 +
                '¿Instalarlo ahora con winget? (pide permisos de administrador y luego reiniciar el PC)' + #13#10 +
                'Elija «No» para abrir la página de descarga y salir.', mbConfirmation, MB_YESNOCANCEL) of
      IDYES:
        begin
          if Exec('winget.exe', 'install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements',
                  '', SW_SHOW, ewWaitUntilTerminated, Code) and (Code = 0) then
            DockerRecienInstalado := True
          else
          begin
            MsgBox('No se pudo instalar Docker Desktop con winget. Instálelo desde https://www.docker.com/products/docker-desktop/ y vuelva a ejecutar este instalador.', mbError, MB_OK);
            Result := False;
          end;
        end;
      IDNO:
        begin
          ShellExec('open', 'https://www.docker.com/products/docker-desktop/', '', '', SW_SHOW, ewNoWait, Code);
          Result := False;
        end;
    else
      Result := False;
    end;
  end;
end;

procedure InitializeWizard();
begin
  AdminPage := CreateInputQueryPage(wpSelectTasks, 'Primer administrador',
    'Cuenta ADMIN con la que entrará por primera vez',
    'Use datos ficticios o de prueba. La contraseña es temporal: Aurora pedirá cambiarla al ingresar. ' +
    'Si ya tiene Aurora instalada, deje el RUT vacío.');
  AdminPage.Add('RUT (ej. 11111111-1):', False);
  AdminPage.Add('Nombre:', False);
  AdminPage.Add('Correo:', False);
  AdminPage.Add('Contraseña temporal (mínimo 10 caracteres, con letras y números):', True);
  PuertoPage := CreateInputQueryPage(AdminPage.ID, 'Puerto', 'Dirección local de Aurora',
    'Aurora quedará en http://localhost:<puerto>, solo accesible desde este PC.');
  PuertoPage.Add('Puerto:', False);
  PuertoPage.Values[0] := '8080';
end;

function TieneLetraYNumero(S: String): Boolean;
var i: Integer; L, N: Boolean;
begin
  L := False; N := False;
  for i := 1 to Length(S) do
  begin
    if (S[i] >= '0') and (S[i] <= '9') then N := True
    else if ((S[i] >= 'a') and (S[i] <= 'z')) or ((S[i] >= 'A') and (S[i] <= 'Z')) then L := True;
  end;
  Result := L and N;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var p: Integer;
begin
  Result := True;
  if (CurPageID = AdminPage.ID) and (Trim(AdminPage.Values[0]) <> '') then
  begin
    if (Trim(AdminPage.Values[1]) = '') or (Pos('@', AdminPage.Values[2]) = 0) then
    begin
      MsgBox('Complete el nombre y un correo válido.', mbError, MB_OK); Result := False;
    end
    else if (Length(AdminPage.Values[3]) < 10) or not TieneLetraYNumero(AdminPage.Values[3]) then
    begin
      MsgBox('La contraseña debe tener al menos 10 caracteres, con letras y números.', mbError, MB_OK); Result := False;
    end;
  end;
  if CurPageID = PuertoPage.ID then
  begin
    p := StrToIntDef(Trim(PuertoPage.Values[0]), 0);
    if (p < 1024) or (p > 65535) then
    begin
      MsgBox('Ingrese un puerto entre 1024 y 65535.', mbError, MB_OK); Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var Datos: TArrayOfString;
begin
  // Los datos del ADMIN van a {tmp}, que Inno Setup borra al terminar; configurar.ps1 además lo borra al leerlo
  if (CurStep = ssInstall) and (Trim(AdminPage.Values[0]) <> '') then
  begin
    SetArrayLength(Datos, 4);
    Datos[0] := Trim(AdminPage.Values[0]); Datos[1] := Trim(AdminPage.Values[1]);
    Datos[2] := Trim(AdminPage.Values[2]); Datos[3] := AdminPage.Values[3];
    SaveStringsToUTF8File(ExpandConstant('{tmp}\admin.txt'), Datos, False);
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = wpFinished) and DockerRecienInstalado then
    WizardForm.FinishedLabel.Caption :=
      'Se instaló Docker Desktop. Reinicie el PC, abra Docker Desktop y acepte sus condiciones; ' +
      'después ejecute «Terminar configuración de Aurora» desde el menú Inicio.';
end;
