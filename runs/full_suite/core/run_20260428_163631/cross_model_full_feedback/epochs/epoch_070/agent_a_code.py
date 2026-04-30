def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = manh(sx, sy, rx, ry)
            do = manh(ox, oy, rx, ry)
            adv = do - ds
            key = (adv, -ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
        best = None
        best_score = None
        for dx, dy, nx, ny in legal:
            ds_new = manh(nx, ny, tx, ty)
            do_new = manh(nx, ny, ox, oy)
            do_res = manh(ox, oy, tx, ty)
            my_adv_next = do_res - ds_new
            # If we can still be the closer agent to the target, prioritize; otherwise pivot to reduce our loss.
            score = (my_adv_next * 10) - ds_new + (do_new * 0.02)
            # Mild bias to avoid dead-ends: prefer moving that doesn't increase distance to the nearest resource too much.
            min_other = 10**9
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if d < min_other:
                    min_other = d
            score -= max(0, min_other - manh(sx, sy, tx, ty)) * 0.2
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources: move toward center-ish while staying somewhat away from opponent
    cx, cy = w // 2, h // 2
    best = (0, 0)
    best_score = None
    for dx, dy, nx, ny in legal:
        score = -manh(nx, ny, cx, cy) + manh(nx, ny, ox, oy) * 0.02
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]