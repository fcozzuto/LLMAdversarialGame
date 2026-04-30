def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    rem = observation["remaining_resource_count"]
    occ = obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def dist(a,b,c,d): 
        dx = a-c; dy = b-d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Choose best resource to target based on relative closeness
    if rem > 0 and resources:
        best = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            val = (do - ds) * 1000 - ds  # prefer resources we're closer to, then nearer
            if best is None or val > best[0] or (val == best[0] and ds < best[1]):
                best = (val, ds, rx, ry)
        _, _, tx, ty = best
    else:
        # If no resources, move to center-ish to be harder to catch
        tx, ty = w // 2, h // 2

    opp_curr = dist(sx, sy, ox, oy)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        ds_next = dist(nx, ny, tx, ty)
        do_next = dist(ox, oy, tx, ty)
        rel_val = (do_next - ds_next) * 1000 - ds_next
        opp_next = dist(nx, ny, ox, oy)
        # Strategic change: when behind, prioritize increasing separation; when ahead, continue resource pressure
        separation_gain = (opp_next - opp_curr)
        pressure = 1 if (rel_val > 0) else -1
        score = rel_val + pressure * separation_gain * 25 - ds_next * 2
        candidates.append((score, ds_next, -opp_next, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]