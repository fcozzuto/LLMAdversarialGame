def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def kdist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def best_resource():
        if not resources:
            return None
        best = None
        best_val = -10**9
        for r in resources:
            rv = kdist((sx, sy), r)
            ov = kdist((ox, oy), r)
            val = (ov - rv) * 3 - rv  # prefer resources we reach sooner
            if val > best_val:
                best_val = val
                best = r
        return best

    target = best_resource()
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    oppd = kdist((sx, sy), (ox, oy))
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is None:
            tdist = oppd
        else:
            tdist = kdist((nx, ny), target)
        nd_to_opp = kdist((nx, ny), (ox, oy))
        score = -tdist * 10 + nd_to_opp * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer closer to target, then farther from opponent
            cur_t = kdist((sx+best_move[0], sy+best_move[1]), target) if target is not None else 0
            cand_t = tdist
            if cand_t < cur_t:
                best_move = (dx, dy)
            elif cand_t == cur_t:
                cur_o = kdist((sx+best_move[0], sy+best_move[1]), (ox, oy))
                if nd_to_opp > cur_o:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]