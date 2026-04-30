def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick target resources: prioritize those we can reach no later than opponent.
    best_target = None
    best_score = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Score: prefer winning (md-od smaller), then closer overall, then deterministic tie-break.
        s1 = md - od
        s2 = md
        s3 = rx * 10 + ry
        cand = (s1, s2, s3)
        if best_score is None or cand < best_score:
            best_score = cand
            best_target = (rx, ry)

    rx, ry = best_target
    # Move: minimize my distance to target; if tie, reduce opponent distance; avoid obstacles/out of bounds.
    best_move = (0, 0)
    best_cmp = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        md = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Ensure we also slightly discourage moves that let opponent be strictly closer.
        adv = md - od
        cmp = (adv, md, (nx * 10 + ny))
        if best_cmp is None or cmp < best_cmp:
            best_cmp = cmp
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]