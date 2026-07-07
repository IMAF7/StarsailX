; Inno Setup — StarsailX（卡片式安装选项）
#define MyAppName "StarsailX"
#define MyAppVersion "2.2.2"
#define MyAppPublisher "StarsailX"
#define MyAppExeName "StarsailX.exe"

[Setup]
AppId={{C4D8E2F1-5A7B-4C9E-8D3F-1B6A9E2C4F07}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=release
OutputBaseFilename=StarsailX_Setup_{#MyAppVersion}
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
; 侧栏大图易拉伸变形，安装向导仅用标题栏图标（SetupIconFile）
; WizardImageFile=installer_wizard.bmp
; WizardSmallImageFile=installer_wizard_small.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
SetupAppTitle=安装 {#MyAppName}
SetupWindowTitle=安装 {#MyAppName}
WelcomeLabel1=安装 StarsailX
WelcomeLabel2=按向导完成安装即可使用。
ClickNext=下一步
ClickFinish=完成
SelectDirLabel3=安装位置：
ReadyLabel1=可以开始安装。
ReadyLabel2a=点击「安装」将文件写入所选目录。
FinishedLabel=安装完成
FinishedLabelNoIcons=安装完成。%n%n可勾选下方立即启动。
ButtonInstall=安装(&I)

[Files]
Source: "dist\StarsailX\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Check: CreateDesktopIcon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Check: LaunchAfterInstall; Flags: nowait postinstall skipifsilent

[Code]
var
  OptPage: TWizardPage;
  CardDesktop: TNewRadioButton;
  CardMenuOnly: TNewRadioButton;
  CardLaunch: TNewCheckBox;

function CreateDesktopIcon: Boolean;
begin
  Result := Assigned(CardDesktop) and CardDesktop.Checked;
end;

function LaunchAfterInstall: Boolean;
begin
  Result := Assigned(CardLaunch) and CardLaunch.Checked;
end;

procedure InitializeWizard;
begin
  OptPage := CreateCustomPage(wpSelectDir, '安装选项', '选择快捷方式');

  CardDesktop := TNewRadioButton.Create(OptPage);
  CardDesktop.Parent := OptPage.Surface;
  CardDesktop.Left := ScaleX(8);
  CardDesktop.Top := ScaleY(8);
  CardDesktop.Width := OptPage.SurfaceWidth - ScaleX(16);
  CardDesktop.Height := ScaleY(56);
  CardDesktop.Caption := '桌面 + 开始菜单' + #13#10 + '在开始菜单和桌面创建快捷方式';
  CardDesktop.Checked := True;
  CardDesktop.Font.Size := 10;

  CardMenuOnly := TNewRadioButton.Create(OptPage);
  CardMenuOnly.Parent := OptPage.Surface;
  CardMenuOnly.Left := ScaleX(8);
  CardMenuOnly.Top := ScaleY(76);
  CardMenuOnly.Width := OptPage.SurfaceWidth - ScaleX(16);
  CardMenuOnly.Height := ScaleY(56);
  CardMenuOnly.Caption := '仅开始菜单' + #13#10 + '只在开始菜单创建快捷方式';
  CardMenuOnly.Font.Size := 10;

  CardLaunch := TNewCheckBox.Create(OptPage);
  CardLaunch.Parent := OptPage.Surface;
  CardLaunch.Left := ScaleX(8);
  CardLaunch.Top := ScaleY(152);
  CardLaunch.Width := OptPage.SurfaceWidth - ScaleX(16);
  CardLaunch.Height := ScaleY(32);
  CardLaunch.Caption := '安装完成后立即启动';
  CardLaunch.Checked := True;
  CardLaunch.Font.Size := 10;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = wpSelectTasks);
end;
