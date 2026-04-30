def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    def step_towards(s, t):
        sx, sy = s
        tx, ty = t
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    def best_resource_target():
        if not resources:
            return (w // 2, h // 2), True
        best = None
        for rx, ry in resources:
            sd = d2((sx, sy), (rx, ry))
            od = d2((ox, oy), (rx, ry))
            # prefer contested where we are not worse; otherwise prefer to attack closer region
            key = (1 if sd <= od else 0, -abs(sd - od), -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry), sd <= od)
        return best[1], best[2]

    target, we_can_take_next = best_resource_target()

    # If opponent is closer to every nearby resource, cut off: head toward the "front" point
    # between opponent and target, biased to land closer to opponent than the target itself.
    if resources and not we_can_take_next:
        # choose closest resource to opponent as its likely next, then intercept near its line
        near = None
        for rx, ry in resources:
            od = d2((ox, oy), (rx, ry))
            if near is None or od < near[0]:
                near = (od, (rx, ry))
        rx, ry = near[1]
        # intercept point: move one step from opponent toward the resource
        ix, iy = ox, oy
        dx, dy = step_towards((ox, oy), (rx, ry))
        ix += dx
        iy += dy
        if inb(ix, iy) and (ix, iy) not in obstacles:
            target = (ix, iy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Main objective: increase our value while reducing opponent's value
        my_res = 0
        opp_res = 0
        if resources:
            # Evaluate only the top few closest resources deterministically
            cand = []
            for rx, ry in resources:
                cand.append((d2((nx, ny), (rx, ry)), d2((ox, oy), (rx, ry)), rx, ry))
            cand.sort(key=lambda x: (x[0], -x[1], -x[2], -x[3]))
            cand = cand[:5]
            for sd, od, rx, ry in cand:
                # if we can be closer than opponent at that resource, it's valuable
                if sd <= od:
                    my_res += 50000 // (1 + sd)
                else:
                    opp_res += 50000 // (1 + sd)
                # also penalize moving away from the best strategic target
            # extra tie-breaker toward target
        dist_to_target = d2((nx, ny), target)
        dist_to_opp = d2((nx, ny), (ox, oy))

        # Two modes: when we can take a resource, prioritize target; otherwise prioritize proximity/blocking
        if resources and we_can_take_next:
            score = (-dist_to_target, dist_to_opp, my_res - opp_res, -nx, -ny)
        else:
            # Block: move closer to where opponent would go (target) and also closer to opponent
            score = (-dist_to_target, dist_to_opp, my_res - opp_res, -(abs(nx - target[0]) + abs(ny - target[1])))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]