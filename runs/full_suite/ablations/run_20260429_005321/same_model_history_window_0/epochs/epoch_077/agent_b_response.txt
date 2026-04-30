def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def cheb(a, b):  # Chebyshev distance (diagonal moves allowed)
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx if dx > 0 else -dx if dx < 0 else 0 if dx == 0 else -dx

    # Correct cheb without branching complexity
    def dist(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        return (nx, ny) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    me = (x, y)
    opp = (ox, oy)

    # Pick target resource we can reach with advantage over opponent.
    if resources:
        best = None
        for r in resources:
            r = (r[0], r[1])
            dm = dist(me, r)
            do = dist(opp, r)
            # Prefer resources closer to me and relatively farther from opponent; slight bias to my distance.
            score = (dm - do) * 10 + dm
            if best is None or score < best[0] or (score == best[0] and dm < best[1]):
                best = (score, dm, r)
        target = best[2]
    else:
        target = (w // 2, h // 2)

    # Score next moves: aim at target, avoid obstacles, and occasionally reduce opponent access to target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        nm = (nx, ny)
        d_t = dist(nm, target)
        d_o_to_target = dist(opp, target)
        # If we are already closer, prioritize reducing distance; otherwise block by moving towards resources where opponent is close.
        val = d_t * 2 - (d_o_to_target - d_t)  # prefer states that keep us ahead
        # Extra penalty for moving near opponent when it doesn't help
        if dist(nm, opp) <= 1 and d_t > dist(me, target):
            val += 3
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]