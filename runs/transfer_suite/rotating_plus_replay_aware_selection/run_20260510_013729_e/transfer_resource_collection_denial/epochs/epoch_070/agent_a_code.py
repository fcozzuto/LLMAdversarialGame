def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Consider only the most relevant resources to keep logic small and deterministic.
    # Prefer resources closer to self, but also include any where opponent is much closer (possible denial).
    scored = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        scored.append((sd, od, rx, ry))
    scored.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
    top = []
    # First by closeness to self
    top.extend([(t[2], t[3]) for t in scored[:6]])
    # Then include some where opponent is closer (to attempt denial)
    scored2 = sorted(scored, key=lambda t: (- (t[1] - t[0]), t[1], t[2], t[3]))
    for t in scored2[:4]:
        p = (t[2], t[3])
        if p not in top:
            top.append(p)
    if not top:
        top = [(resources[0][0], resources[0][1])]

    def eval_pos(px, py):
        best = -10**18
        best_sd = 10**18
        for rx, ry in top:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Positive means we are closer (advantage).
            adv = od - sd
            # If opponent is closer, strongly prefer resources where we can still catch up.
            score = adv * 1000 - sd
            if score > best or (score == best and (sd < best_sd)):
                best = score
                best_sd = sd
        return best

    best_move = (0, 0)
    best_val = -10**30
    # If both can grab quickly, also bias toward moves that reduce nearest self distance.
    cur_sd_near = min(man(sx, sy, rx, ry) for rx, ry in top)
    cur_od_near = min(man(ox, oy, rx, ry) for rx, ry in top)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        val = eval_pos(nx, ny)
        nsd = min(man(nx, ny, rx, ry) for rx, ry in top)
        nod = cur_od_near
        val += (cur_sd_near - nsd) * 2
        # Small deterministic tie-breaker: lexicographic preference toward lower dx, then dy
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]