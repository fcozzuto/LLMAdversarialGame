def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b):  # Chebyshev distance
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best resource to get ahead (prefer capturing-first).
    target = None
    best_adv = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        sd = md((sx, sy), (rx, ry))
        od = md((ox, oy), (rx, ry))
        adv = od - sd
        key = (adv, -sd, -md((ox, oy), (rx, ry)))
        if target is None or key > best_adv:
            best_adv = key
            target = (rx, ry)

    # If no resources, contest by moving toward opponent.
    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    # Evaluate moves: approach target, keep distance from opponent, avoid obstacles.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            val = -10**9
        else:
            me_to = md((nx, ny), (tx, ty))
            opp_to = md((ox, oy), (tx, ty))
            # Encourage being closer than opponent after the move; also avoid getting too close to opponent.
            val = (opp_to - me_to) * 20 - me_to * 3 + (md((nx, ny), (ox, oy)) * 1)
            # If we step onto a resource, spike.
            if (nx, ny) in obstacles:
                val -= 1000
            else:
                for rx, ry in resources:
                    if rx == nx and ry == ny and (rx, ry) not in obstacles:
                        val += 200
                        break
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]