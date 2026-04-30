def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Chebyshev distance (diagonal moves allowed)
    def dist(a, b):
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx if dx > dy else dy
    # clamp to grid and treat obstacles as blocked (engine would reject, but we keep deterministic)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_mv = (0, 0)
    best_score = -10**18

    # If no resources visible, drift to center-ish while keeping away from obstacles
    if not resources:
        tx, ty = w//2, h//2
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            score = -dist((nx, ny), (tx, ty)) - 0.1*dist((nx, ny), (ox, oy))
            if score > best_score:
                best_score = score; best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]

    # Evaluate each move by best achievable "resource advantage" next.
    # advantage = (dist_opp_to_r - dist_self_to_r): larger means we reach sooner than opponent.
    # add small preference for generally getting closer too.
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        new_self = (nx, ny)
        best_adv = -10**18
        closest_self = 10**18
        closest_opp = 10**18
        for r in resources:
            ar = tuple(r)
            d_s = dist(new_self, ar)
            d_o = dist((ox, oy), ar)
            if d_s < closest_self: closest_self = d_s
            if d_o < closest_opp: closest_opp = d_o
            adv = d_o - d_s
            if adv > best_adv: best_adv = adv
        # Encourage reaching some resource with high advantage; also avoid getting too close to opponent (risk collision/contestation)
        score = best_adv * 1000 - closest_self * 2 - 0.3*dist(new_self, (ox, oy)) + 0.1*(closest_opp)
        # Tie-break deterministically by preferring non-staying then lexicographic move ordering
        if score > best_score:
            best_score = score; best_mv = (dx, dy)
        elif score == best_score:
            if best_mv == (0, 0) and (dx, dy) != (0, 0):
                best_mv = (dx, dy)
            elif (dx, dy) != best_mv and (dx, dy) < best_mv:
                best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]