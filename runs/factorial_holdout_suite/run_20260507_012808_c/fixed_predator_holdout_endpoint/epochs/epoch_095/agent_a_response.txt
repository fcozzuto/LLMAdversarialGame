def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    # If opponent is denying, prioritize resources where we can arrive no later.
    best = None
    for tx, ty in resources:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        advantage = od - md
        # prefer md small, advantage large; discourage paths into opponent-favoring region
        toward_me = (tx - sx) * (sx - ox) + (ty - sy) * (sy - oy)
        quad_bias = 0.5 if toward_me >= 0 else -0.5
        score = (advantage * 10.0) - (md * 1.0) + quad_bias
        if best is None or score > best[0]:
            best = (score, tx, ty)
    _, tx, ty = best

    # Greedy step toward target, with deterministic fallback among legal moves.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    visited = set()
    for cdx, cdy in candidates:
        if (cdx, cdy) in visited:
            continue
        visited.add((cdx, cdy))
        nx = clamp(sx + cdx, 0, w - 1)
        ny = clamp(sy + cdy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        # tie-break: prefer move that improves our distance and worsens opponent's
        my_next = cheb(nx, ny, tx, ty)
        opp_next = cheb(nx, ny, ox, oy)
        # also keep short-term target closeness
        if best is None:
            return [cdx, cdy]
        # choose first legal; order already deterministic and favors approach
        return [cdx, cdy]

    return [0, 0]