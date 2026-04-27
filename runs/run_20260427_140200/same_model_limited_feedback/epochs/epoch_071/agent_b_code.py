def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick resource where we have the biggest distance advantage (opp closer => lower adv; we want ours closer)
    target = None
    best = None
    for r in resources:
        d_self = dist((sx, sy), r)
        d_opp = dist((ox, oy), r)
        adv = d_opp - d_self  # higher is better
        key = (adv, -d_self)  # tie-break: closer to us
        if best is None or key > best:
            best = key
            target = r
    if target is None:
        # No visible resources: drift toward center while avoiding obstacles
        target = (w // 2, h // 2)

    opp_to_target = dist((ox, oy), target)
    cur_to_opp = dist((sx, sy), (ox, oy))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), target)
        d_opp = dist((ox, oy), target)
        # Encourage: get to target sooner; discourage: get too close to opponent (risk of losing)
        score = (-d_self) + 0.25 * (cur_to_opp - dist((nx, ny), (ox, oy)))
        # If opponent also close to target, prefer moves that increase our advantage
        score += 0.15 * (d_opp - d_self)
        # Slightly prefer moves that reduce opponent-target distance in case of contesting (interference)
        score += 0.05 * (-opp_to_target)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        return [0, 0]
    return [dx, dy]