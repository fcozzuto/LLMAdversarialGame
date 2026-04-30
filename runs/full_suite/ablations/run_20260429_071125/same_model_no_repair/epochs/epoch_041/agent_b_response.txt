def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d_cheb(ax, ay, bx, by): 
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource we can realistically secure
    best_t = None
    best_t_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        us = d_cheb(sx, sy, rx, ry)
        op = d_cheb(ox, oy, rx, ry)
        # Favor closer to us and farther from opponent
        val = us - 1.05 * op
        if best_t_val is None or val < best_t_val:
            best_t_val = val
            best_t = (rx, ry)
    if best_t is None:
        best_t = resources[0]
    tx, ty = best_t

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = d_cheb(nx, ny, tx, ty)
        opp_d = d_cheb(ox, oy, tx, ty)

        # Encourage getting closer than the opponent
        score = our_d - 0.7 * opp_d

        # If we'd be losing the race to this target, penalize
        if opp_d + 0 < our_d:
            score += 2.5

        # Small bias to keep moving (reduce dithering)
        score += 0.15 * (1 if dx == 0 and dy == 0 else 0)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]