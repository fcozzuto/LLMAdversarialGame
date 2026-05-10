def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = (sp[0], sp[1]) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (op[0], op[1]) if isinstance(op, (list, tuple)) and len(op) >= 2 else (sx, sy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or observation.get("unclaimed") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    best = None
    best_key = None

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if unclaimed:
            md = min(manh(nx, ny, ux, uy) for ux, uy in unclaimed)
            key = (md, dx, dy)
        else:
            dd = manh(nx, ny, ox, oy)
            key = (-dd, dx, dy)
        if best is None or key < best_key:
            best = [dx, dy]
            best_key = key

    return best if best is not None else [0, 0]