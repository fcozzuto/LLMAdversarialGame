def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_dist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < md:
                md = d
        return md

    my_md = best_resource_dist(sx, sy)
    op_md = best_resource_dist(ox, oy)
    deny_mode = my_md > op_md  # opponent closer -> try to deny; else collect

    best_move = (0, 0)
    best_val = -10**18

    # tie-break: prioritize moves that immediately land on a resource
    res_set = set(resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # base: collect value = - our distance to nearest resource
        our_d = best_resource_dist(nx, ny)

        # denial: estimate if opponent can beat us to a promising resource
        # compute our advantage over opponent for resources, then choose best
        if deny_mode:
            adv = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                od = cheb(ox, oy, rx, ry)
                nd = cheb(nx, ny, rx, ry)
                # higher means we are closer (or opponent farther)
                v = od - nd
                if v > adv:
                    adv = v
            val = (1000 if (nx, ny) in res_set else 0) + adv * 10 - our_d
        else:
            # collect mode: strongly prefer reduction to nearest and potential capture
            val = (1000 if (nx, ny) in res_set else 0) + (-our_d) * 10

            # slight denial pressure: avoid moves that put us much farther than opponent
            op_near_next = best_resource_dist(ox, oy)
            val += (op_near_next - our_d)

        # deterministic tie-break: keep smaller (dx,dy) lexicographically among equals
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]