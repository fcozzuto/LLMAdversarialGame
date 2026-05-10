def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    pursuer = not any(k in role for k in ("evader", "runner", "fugitive"))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def manh(a, b, c, d): return abs(a-c) + abs(b-d)

    best_moves = []
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        val = -d if pursuer else d
        if best_val is None or val > best_val:
            best_val = val
            best_moves = [(dx, dy)]
        elif val == best_val:
            best_moves.append((dx, dy))

    if best_moves:
        best_moves.sort()
        return [best_moves[0][0], best_moves[0][1]]

    return [0, 0]