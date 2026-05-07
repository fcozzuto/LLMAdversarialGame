def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8

    obst_list = observation.get("obstacles", []) or []
    obstacles = set()
    for o in obst_list:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((o[0], o[1]))
        elif isinstance(o, dict) and "x" in o and "y" in o:
            obstacles.add((o["x"], o["y"]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_list = observation.get("resources", []) or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((r[0], r[1]))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((r["position"][0], r["position"][1]))
            elif "x" in r and "y" in r:
                resources.append((r["x"], r["y"]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        best_d = None
        best_move = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = min(man(nx, ny, rx, ry) for rx, ry in resources)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d, best_move = d, (dx, dy)
        if best_move is None:
            best_move = min(moves)
        return [int(best_move[0]), int(best_move[1])]

    best = None
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = man(nx, ny, ox, oy)
        score = -d
        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best, best_move = score, (dx, dy)
    if best_move is None:
        best_move = min(moves)
    return [int(best_move[0]), int(best_move[1])]