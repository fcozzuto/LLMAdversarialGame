def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(rx, ry):
        if (rx, ry) in obstacles:
            return 10**9
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach much sooner than opponent; break ties by closeness.
        return (du - 1.35 * do) * 100 + du

    if not resources:
        return [0, 0]

    best_t = None
    best_v = 10**9
    for rx, ry in resources:
        v = score_target(rx, ry)
        if v < best_v:
            best_v = v
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_m = (0, 0)
    best_m_v = 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_next = cheb(nx, ny, tx, ty)
        opp_next = cheb(ox, oy, tx, ty)
        # Keep moving to reduce our distance; if opponent is closer, slightly emphasize blocking their advantage.
        v = our_next * 10 - (opp_next - our_next) * 4
        # Mild preference to stay off obstacles adjacency (deterministic local safety).
        adj_pen = 0
        for ax, ay in ((nx-1, ny),(nx+1, ny),(nx, ny-1),(nx, ny+1)):
            if (ax, ay) in obstacles:
                adj_pen += 1
        v += adj_pen
        if v < best_m_v:
            best_m_v = v
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]