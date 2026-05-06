def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def best_resource_target_from(nx, ny):
        if not resources:
            return 0, 0, None
        best_gain = -10**18
        best_self_d = 10**18
        best_cell = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer (denial), but also keep progressing.
            gain = (opp_d - self_d) * 1000 - self_d
            if self_d == 0:
                gain += 10**9
            if gain > best_gain or (gain == best_gain and (self_d < best_self_d or (self_d == best_self_d and (rx, ry) < best_cell))):
                best_gain = gain
                best_self_d = self_d
                best_cell = (rx, ry)
        return best_gain, best_self_d, best_cell

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            v = d * 1000 + (nx - (w - 1)) * 0 + (ny - (h - 1)) * 0
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    cur_best_move = [0, 0]
    cur_best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        gain, self_d, tgt = best_resource_target_from(nx, ny)
        # Small tie-breaks: avoid moving toward opponent when denial isn't possible.
        opp_sep = cheb(nx, ny, ox, oy)
        # If we can take a resource immediately, prioritize strongly.
        immediate = 1 if tgt is not None and tgt == (nx, ny) else 0
        val = gain + immediate * 10**8 + opp_sep
        if val > cur_best_val or (val == cur_best_val and (dx, dy) < (cur_best_move[0], cur_best_move[1])):
            cur_best_val = val
            cur_best_move = [dx, dy]
    return cur_best_move