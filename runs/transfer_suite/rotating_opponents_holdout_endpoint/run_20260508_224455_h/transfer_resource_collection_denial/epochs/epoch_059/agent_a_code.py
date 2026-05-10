def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            nx = x + dx
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    best_move = [0, 0]
    best_score = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue

            # Choose the resource that maximizes our advantage after this move.
            best_cell_score = -10**18
            adj_pen = obstacle_adj(nx, ny)
            for rx, ry in resources:
                rx, ry = int(rx), int(ry)
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)

                # Big preference for resources we can reach strictly earlier,
                # otherwise still try to reduce opponent lead.
                lead = opp_d - our_d
                can_take = 1 if our_d < opp_d else 0
                # Small tie-break pressure to avoid wandering.
                s = can_take * 1_000_000 + lead * 1000 - our_d * 3 - adj_pen * 5
                if s > best_cell_score:
                    best_cell_score = s

            if best_cell_score > best_score:
                best_score = best_cell_score
                best_move = [dx, dy]

    return best_move