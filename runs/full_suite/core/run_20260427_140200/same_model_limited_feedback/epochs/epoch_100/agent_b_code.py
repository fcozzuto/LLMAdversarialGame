def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir

    def nearest_from(px, py):
        best = None
        bd = 10**9
        for rx, ry in resources:
            d = dist((px, py), (rx, ry))
            if d < bd:
                bd = d
                best = (rx, ry)
        return best, bd

    own_t, own_d = nearest_from(sx, sy)
    opp_t, opp_d = nearest_from(ox, oy)

    # If opponent is about to grab something, bias toward intercepting that resource.
    immediate_threat = None
    min_opp_next = 10**9
    for rx, ry in resources:
        d = dist((ox, oy), (rx, ry))
        if d <= 1:
            immediate_threat = (rx, ry)
            break
        if d < min_opp_next:
            min_opp_next = d
    target = immediate_threat if immediate_threat is not None else own_t

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    ordered = []
    for dy in dys:
        for dx in dxs:
            ordered.append((dx, dy))
    # Deterministic preference: stay last? We'll score anyway; tie-break by order.

    best_move = (0, 0)
    best_score = -10**18

    opp_goal = opp_t
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_self = dist((nx, ny), target)
        d_own_to_opp = dist((nx, ny), (ox, oy))
        d_opp_to_own = dist((ox, oy), target)

        # Encourage getting closer to own target, and discourage letting opponent be closer.
        score = 0.0
        score += (10 - d_self) * 2.0
        score += (d_opp_to_own - d_self) * 1.2  # if we get closer than them, boost
        score += d_own_to_opp * 0.03          # slight separation

        # If we can potentially take a resource this turn, prioritize it.
        can_take = 0
        for rx, ry in resources:
            if (nx, ny) == (rx, ry):
                can_take = 1
                break
        if can_take:
            score += 50.0

        # Additional bias: if threatened, also move to worsen opponent's approach to their nearest target.
        if immediate_threat is not None and opp_goal is not None:
            score += (dist((nx, ny), opp_goal) - dist((sx, sy), opp_goal)) * 0.8

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]