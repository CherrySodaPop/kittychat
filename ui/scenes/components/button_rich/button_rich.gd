@tool
class_name ButtonRich extends Button

@export var rich_text_label:RichTextLabel = null

func _process(_delta:float) -> void:
	rich_text_label.text = text
