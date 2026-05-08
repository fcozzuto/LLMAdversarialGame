def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    targets = set()
    targets |= unclaimed
    targets |= resources
    if not targets:
        return [0, 0]

    tlist = sorted(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    tx, ty = tlist[0]

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            dist_t = abs(nx - tx) + abs(ny - ty)
            score = 0
            if (nx, ny) in resources:
                score += 1000
            if (nx, ny) in unclaimed:
                score += 100
            # Favor getting closer to target and away from opponent
            dist_op = abs(nx - ox) + abs(ny - oy)
            score += (200 - 10 * dist_t) + (dist_op // 2)
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]