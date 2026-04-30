def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = w // 2, h // 2
    center = (cx, cy)

    # If resources exist: pick move that maximizes "we arrive sooner" advantage vs opponent.
    # If none: drift to center while keeping some distance from opponent.
    best_move = (0, 0)
    best_val = -10**18
    best_tiebreak = None

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue
        new_pos = (nx, ny)

        if resources:
            # Max over resources: prefer the resource where our arrival is most ahead of opponent.
            # Opponent assumed stationary for deterministic proxy; still changes move choice materially.
            best_adv = -10**18
            for rx, ry in resources:
                rpos = (rx, ry)
                our_d = dist(new_pos, rpos)
                opp_d = dist((ox, oy), rpos)
                adv = (opp_d - our_d)
                # Small preference for closer-than-opp and for actually landing on a resource.
                if rpos == new_pos:
                    adv += 6.0
                # Discourage moving away from center only slightly to avoid corner-trapping ourselves.
                adv -= 0.02 * dist(new_pos, center)
                if adv > best_adv:
                    best_adv = adv
            val = best_adv
        else:
            # No resources: go toward center, but avoid giving opponent approach advantage.
            val = -dist(new_pos, center) - 0.15 * (dist(new_pos, (ox, oy)))

        # Deterministic tie-break: prefer moves that reduce distance to the nearest resource,
        # then prefer diagonal, then lexicographic.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
            if resources:
                nearest_d = min(dist((nx, ny), r) for r in resources)
            else:
                nearest_d = 0
            best_tiebreak = (nearest_d, -(abs(dx) + abs(dy)), dx, dy)
        elif val == best_val:
            if resources:
                nearest_d = min(dist((nx, ny), r) for r in resources)
            else:
                nearest_d = 0
            tiebreak = (nearest_d, -(abs(dx) + abs(dy)), dx, dy)
            if best_tiebreak is None or tiebreak < best_tiebreak:
                best_move = (dx, dy)
                best_tiebreak = tiebreak

    return [int(best_move[0]), int(best_move[1])]