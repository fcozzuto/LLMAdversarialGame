def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda p: (max(abs(sx - p[0]), abs(sy - p[1])), p[0], p[1]))
    else:
        tx, ty = w // 2, h // 2

    target_dx = 1 if sx < tx else (-1 if sx > tx else 0)
    target_dy = 1 if sy < ty else (-1 if sy > ty else 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = max(abs(nx - tx), abs(ny - ty))
        step_pref = (dx == target_dx and dy == target_dy)
        score = (dist, 0 if step_pref else 1, abs(dx) + abs(dy), dx, dy)
        if best is None or score < best_score:
            best = [dx, dy]
            best_score = score

    if best is not None:
        return best
    for dx, dy in [(target_dx, 0), (0, target_dy), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]