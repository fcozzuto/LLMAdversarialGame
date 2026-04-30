def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def best_resource_opportunity(nx, ny):
        if not resources:
            return -(manh(nx, ny, ox, oy))
        best = -10**18
        for rx, ry in resources:
            d_me = manh(nx, ny, rx, ry)
            d_op = manh(ox, oy, rx, ry)
            # Prefer stealing/contesting: being closer than opponent.
            steal = (d_op - d_me)
            # Also prefer nearer picks once contested.
            pick = -d_me
            # If opponent is closer, add pressure to deny by moving away from that resource.
            block = -max(0, d_me - d_op) * 2
            v = steal * 3 + pick + block
            if v > best:
                best = v
        return best

    # If resources are still present, contest; otherwise, herd away from opponent.
    my_next_best = [0, 0]
    my_best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        opp_dist = manh(nx, ny, ox, oy)
        res_score = best_resource_opportunity(nx, ny)
        # Additional deterministic opponent pressure: avoid giving adjacent access early.
        opponent_pressure = opp_dist if resources else opp_dist * 2
        # Prefer not stepping onto immediate resource if it would allow instant opponent grab (soft deny).
        immediate = 0
        for rx, ry in resources:
            if manh(nx, ny, rx, ry) == 0:
                # if opponent is also within 1, de-prioritize slightly
                if manh(ox, oy, rx, ry) <= 1:
                    immediate = -5
                break
        score = res_score + opponent_pressure + immediate
        if score > my_best_score:
            my_best_score = score
            my_next_best = [dx, dy]

    # Safety fallback (shouldn't trigger if staying is legal).
    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return my_next_best