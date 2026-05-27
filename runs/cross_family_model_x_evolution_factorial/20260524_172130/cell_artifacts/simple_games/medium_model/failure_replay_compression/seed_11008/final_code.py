def choose_move(observation):
    grid = observation.get("grid", {})
    pos = observation.get("position", grid.get("position", (0, 0)))
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        x, y = pos[0], pos[1]
    else:
        x, y = 0, 0

    height = grid.get("height", 1)
    width = grid.get("width", 1)
    cx, cy = (width // 2, height // 2)

    dx = 0
    dy = 0

    if x < cx:
        dx = 1
    elif x > cx:
        dx = -1
    if y < cy:
        dy = 1
    elif y > cy:
        dy = -1

    if dx not in (-1, 0, 1):
        dx = 0
    if dy not in (-1, 0, 1):
        dy = 0

    return [dx, dy]
