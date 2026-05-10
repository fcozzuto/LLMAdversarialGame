def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # Bias: reduce Manhattan components toward the opponent, and avoid "wasting" diagonals.
        md_before = abs(sx - ox) + abs(sy - oy)
        md_after = abs(nx - ox) + abs(ny - oy)
        md_improve = md_before - md_after

        # Bias away from increasing distance while still equal dist2.
        gx = 0 if ox == sx else (1 if ox > sx else -1)
        gy = 0 if oy == sy else (1 if oy > sy else -1)
        align = (1 if dx == gx else 0) + (1 if dy == gy else 0)
        waste = 1 if (dx != 0 and gx == 0) or (dy != 0 and gy == 0) else 0

        score = (d * 1000) - (md_improve * 50) - (align * 5) + (waste * 2)
        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]