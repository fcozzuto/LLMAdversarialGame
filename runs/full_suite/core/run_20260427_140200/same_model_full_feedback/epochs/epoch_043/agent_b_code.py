def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_move(tx, ty):
        best = None
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = man(nx, ny, tx, ty)
                if d < best_d or (d == best_d and (dx, dy) < best):
                    best_d = d
                    best = (dx, dy)
        return best if best is not None else (0, 0)

    if resources:
        tar = None
        tar_d = 10**9
        # Prefer a resource where we are at least not much further than opponent (deterministic).
        for x, y in resources:
            ds = man(sx, sy, x, y)
            do = man(ox, oy, x, y)
            score = (ds - do, ds, x, y)
            if score < (tar_d, tar_d, tar[0], tar[1]) if tar else True:
                tar = (x, y)
                tar_d = score[0]
        # If tie/logic oddities, still choose nearest to us deterministically.
        if tar is None:
            tar = min(resources, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))
        return list(best_move(tar[0], tar[1]))
    else:
        # No visible resources: move toward opponent's position to contest/capture.
        return list(best_move(ox, oy))