def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Targeting change: intercept resources that opponent is closer to (block), otherwise take our nearest.
    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent is closer, strongly prioritize interception.
        # Otherwise prioritize our nearest, but still slightly prefer neutral positions.
        block_term = (ds - do)  # negative means opponent closer
        score = 0.0
        if do < ds:
            score = 100.0 + (do - ds) * -30.0  # larger when we can catch up / deny
            score += 5.0 * (ds == 0) - 1.0 * (ds > 6)
        else:
            score = (ds * -10.0) + (do - ds) * 1.5
        # Tiny bias to avoid oscillations: favor resources with a deterministic hash.
        score += ((rx * 31 + ry * 17 + 7) % 10) * 0.01
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # If opponent is adjacent to the target, aim for the adjacent square that maximizes distance-from-opponent
    # while still reducing distance to the target.
    need_intercept = cheb(ox, oy, tx, ty) <= 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        base = -ds_next * 6.0
        if need_intercept:
            # Deny by keeping away from opponent while still approaching the target.
            dop = cheb(nx, ny, ox, oy)
            base += dop * 2.2
        else:
            # General: don't allow opponent to immediately steal; slightly prefer moves that increase their distance to target.
            do_next = cheb(ox, oy, tx, ty)
            base += (do_next - cheb(nx, ny, tx, ty)) * 0.3
        # Discourage stepping into dead zones behind obstacles (small deterministic penalty).
        penalty = 0.0
        if (nx + 1, ny) in obstacles or (nx - 1, ny) in obstacles:
            penalty += 0.2
        if (nx, ny + 1) in obstacles or (nx, ny - 1) in obstacles:
            penalty += 0.2
        base -= penalty
        # Deterministic tie-break favor moving closer in Chebyshev, then lower dx, then lower dy.
        if best_step is None or base > best_step or (base == best_step and (ds_next < cheb(sx, sy, tx, ty) or (dx, dy) < best_move)):
            best_step = base
            best_move = (dx, dy)

    # If all moves invalid (should be rare), stay.
    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]