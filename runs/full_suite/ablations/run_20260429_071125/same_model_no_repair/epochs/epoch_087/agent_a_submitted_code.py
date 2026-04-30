def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_block_penalty(x, y):
        # small penalty for being surrounded by obstacles to avoid getting stuck
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    pen += 1
        return pen

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Main change vs prior: instead of robustness across all resources, focus on
    # a "lead-seeking" score: choose a move that maximizes the best resource lead,
    # but if we're not leading any resource, we maximize opponent-distance to resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_lead = None  # lead = opp_dist - self_dist
        best_opp_score = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd
            if best_lead is None or lead > best_lead:
                best_lead = lead
            opp_score = od * 10 - sd  # push opponent away from targets while we still progress
            if best_opp_score is None or opp_score > best_opp_score:
                best_opp_score = opp_score

        opp_adj_pen = 3 if cheb(nx, ny, ox, oy) <= 1 else 0
        blk_pen = adj_block_penalty(nx, ny)

        val = None
        if best_lead > 0:
            # leading somewhere: maximize lead, also prefer shorter self distance to that target indirectly by lead itself
            val = best_lead * 100 - opp_adj_pen * 5 - blk_pen
        else:
            # not leading: pursue denial by making opponent farther from resources while avoiding trap positions
            val = best_opp_score - opp_adj_pen * 8 - blk_pen

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: prefer moves that reduce distance to opponent? actually avoid opponent adjacency
            if opp_adj_pen < (3 if cheb(sx + best_move[0], sy + best_move[1], ox, oy) <= 1 else 0):
                best_move = (dx, dy)
            elif opp_adj_pen == (3 if cheb(sx + best_move[0], sy + best_move[1], ox, oy) <= 1 else 0):
                # then prefer smaller distance to nearest resource (progress)
                curd = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
                oldx, oldy = sx + best_move[0], sy + best_move[1]
                oldd = min(cheb(oldx, oldy, rx, ry) for rx