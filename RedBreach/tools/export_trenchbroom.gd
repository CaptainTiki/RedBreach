extends SceneTree
## Exports a portable game definition; installation into TrenchBroom is a separate copy.

func _initialize() -> void:
	var output := ProjectSettings.globalize_path("res://../tools/trenchbroom/RedBreach")
	DirAccess.make_dir_recursive_absolute(output)
	var config: TrenchBroomGameConfig = load("res://mapping/red_breach_game_config.tres")
	var file := FileAccess.open(output.path_join("GameConfig.cfg"), FileAccess.WRITE)
	file.store_string(config._build_class_text())
	file.close()
	config.fgd_file.do_export_file(FuncGodotFGDFile.FuncGodotTargetMapEditors.TRENCHBROOM, output)
	config.icon.get_image().save_png(output.path_join("icon.png"))
	print("RED_BREACH_CONFIG_EXPORTED: ", output)
	quit()
