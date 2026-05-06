def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        edge = 1 if tx in (0, w - 1) or ty in (0, h - 1) else 0
        center_dist = abs(tx - cx) + abs(ty - cy)
        # Aim to be first while preferring central control; avoid edge grabs when opponent closer.
        val = (od - sd) - 0.6 * edge * (1 if od < sd else 0) - 0.05 * center_dist
        if best is None or val > best[0] or (val == best[0] and (sd < best[2])):
            best = (val, (tx, ty), sd)

    if best is None:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (w - 1 + h - 1 - (sx + sy)) else (0, 0)
    else:
        tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # move toward target; slight repulsion if getting closer to opponent
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        score = -d_to_t + 0.08 * d_to_o
        # discourage stalling unless no progress options
        if dx == 0 and dy == 0:
            score -= 0.02
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves blocked, stay (engine will keep position).
    return [int(best_move[0]), int(best_move[1])]