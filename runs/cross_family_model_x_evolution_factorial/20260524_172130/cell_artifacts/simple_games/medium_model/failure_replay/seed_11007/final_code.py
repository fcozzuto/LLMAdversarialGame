def choose_move(observation):
    # Defensive extraction
    grid = observation.get("grid", [])
    pos = observation.get("position", {})
    x = pos.get("x", 0)
    y = pos.get("y", 0)

    last_move = observation.get("last_move", None)
    if isinstance(last_move, (list, tuple)) and len(last_move) == 2:
        lx, ly = int(last_move[0]), int(last_move[1])
    else:
        lx, ly = 0, 0

    h = observation.get("grid_height", 0)
    w = observation.get("grid_width", 0)

    def clamp(v):
        if v < -1:
            return -1
        if v > 1:
            return 1
        return v

    dx = 0
    dy = 0

    if w and h:
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        tdx = (cx - x)
        tdy = (cy - y)
        adx = abs(tdx)
        ady = abs(tdy)
        if adx == 0 and ady == 0:
            dx, dy = 0, 0
        else:
            dx = clamp(int((tdx) / max(1, adx)))
            dy = clamp(int((tdy) / max(1, ady)))
    else:
        dx = (x + y) % 3 - 1
        dy = ((x * 2 + y) % 3) - 1
        dx = clamp(dx)
        dy = clamp(dy)

    if isinstance(last_move, (list, tuple)) and len(last_move) == 2:
        if dx == 0 and dy == 0:
            dx = -ly
            dy = lx
            dx = clamp(dx)
            dy = clamp(dy)

    # Final defensive tweak: avoid staying in same place when possible by nudging if the last move was also neutral
    if dx == 0 and dy == 0 and isinstance(last_move, (list, tuple)):
        dx = 1 if (x + y) % 2 == 0 else -1
        dy = 0
        dx = clamp(dx)
        dy = clamp(dy)

    return [dx, dy]
