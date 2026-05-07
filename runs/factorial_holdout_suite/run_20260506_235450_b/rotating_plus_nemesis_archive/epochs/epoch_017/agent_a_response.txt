def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    # Different from baseline: use opponent-distance-aware targeting + row/column interference bias
    tr = observation.get("turns_remaining", 0)
    endgame = tr <= 10  # deterministic switch
    best_cell = (sx, sy)
    best_val = -10**18

    # precompute opponent "sweep" preference: resources in same row/column as opponent get less priority
    opp_row = oy
    opp_col = ox

    for r in resources:
        tx, ty = r[0], r[1]
        if not inb(tx, ty): 
            continue
        sd = dist_cheb(sx, sy, tx, ty)
        od = dist_cheb(ox, oy, tx, ty)
        if endgame:
            # finish quickly: just minimize own distance, with slight obstacle-adjacency discouragement later via move eval
            val = -sd
        else:
            # seek positions where we are closer than opponent; also avoid being in opponent's likely sweep line
            row_bias = 2 if ty == opp_row else 0
            col_bias = 2 if tx == opp_col else 0
            # Make it harder to chase when opponent is already much closer
            val = (od - sd) * 3 - sd - row_bias - col_bias
        if val > best_val:
            best_val = val
            best_cell = (tx, ty)

    tx, ty = best_cell

    # Choose among legal next steps by evaluating progress + safety
    def obstacle_pen(x, y):
        pen = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            if (x + ax, y + ay) in obstacles:
                pen += 2
        return pen

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # progress toward target
        prog = dist_cheb(sx, sy, tx, ty) - dist_cheb(nx, ny, tx, ty)
        # avoid letting opponent get significantly closer to the same target
        opp_prog = dist_cheb(ox, oy, tx, ty) - dist_cheb(ox, oy, tx, ty)  # opponent doesn't move here; keep deterministic structure
        # safety: discourage moving adjacent to obstacles and into opponent sweep lines (row/col)
        sweep_pen = (2 if ny == oy else 0) + (2 if nx == ox else 0)
        score = prog * 10 - obstacle_pen(nx, ny) - sweep_pen + (dist_cheb(nx, ny, tx, ty) == 0) * 50
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]