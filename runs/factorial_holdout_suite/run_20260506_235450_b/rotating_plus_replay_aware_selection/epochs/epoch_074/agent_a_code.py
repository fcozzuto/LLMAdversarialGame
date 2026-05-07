def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = int(sx + dx), int(sy + dy)
        if inb(nx, ny) and (nx, ny) not in obs_set:
            legal.append((dx, dy, nx, ny))

    if not legal or not resources:
        return [0, 0]

    # Pick the resource that maximizes our "lead" (opp farther than us), tie-break deterministically.
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = man(int(sx), int(sy), rx, ry)
        od = man(int(ox), int(oy), rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # higher lead, then closer, then prefer larger coords deterministically
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Choose the legal move that most reduces distance to the target; if tie, prefer moves that worsen opponent distance.
    cur_d = man(int(sx), int(sy), tx, ty)
    opp_d = man(int(ox), int(oy), tx, ty)
    best_move = None
    best_mkey = None
    for dx, dy, nx, ny in legal:
        nd = man(nx, ny, tx, ty)
        nod = opp_d + 0  # opponent doesn't move here; use our next step to approximate pressure
        # A tiny obstacle-aware nudge: prefer moves that go to cells with fewer adjacent obstacles.
        adj_obs = 0
        for ax, ay in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obs_set:
                adj_obs += 1
        mkey = (-(nd - cur_d), -adj_obs, -nod, -dx, -dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]