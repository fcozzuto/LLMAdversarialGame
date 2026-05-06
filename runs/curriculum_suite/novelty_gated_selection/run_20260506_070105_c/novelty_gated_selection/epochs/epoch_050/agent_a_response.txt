def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = []
    for r in (observation.get("resources", []) or []):
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target that balances closeness to me and being not too reachable by opponent
    best = None
    for rx, ry in resources:
        my_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        # Prefer resources where I'm closer; penalize ones opponent is closer to.
        # Small bias toward keeping directionality (diagonal-ish alignment).
        align = abs((rx - sx) - (ry - sy))
        sc = (my_d - 1.15 * opp_d) + 0.02 * align
        if best is None or sc < best[0]:
            best = (sc, rx, ry)
    _, tx, ty = best

    # Pick move that reduces my distance to the chosen target and avoids obstacles; also deny opponent progress.
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d2 = dist((nx, ny), (tx, ty))
        opp_d2 = dist((ox, oy), (tx, ty))
        # if I step into a cell that makes opponent relatively closer to same target, penalize
        sc = my_d2 - 0.15 * opp_d2
        if sc < best_move[0]:
            best_move = (sc, dx, dy)

    dx, dy = best_move[1], best_move[2]
    # Final safety: ensure integers in allowed range
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]