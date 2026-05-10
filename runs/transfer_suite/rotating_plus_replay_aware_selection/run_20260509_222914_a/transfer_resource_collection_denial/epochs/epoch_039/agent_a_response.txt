def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resset = set()
    reslist = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            resset.add((px, py))
            reslist.append((px, py))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center_x, center_y = (w - 1) // 2, (h - 1) // 2

    def nearest_res_dist(px, py):
        best = 10**9
        for rx, ry in reslist:
            d = manh(px, py, rx, ry)
            if d < best:
                best = d
        return best if reslist else 10**9

    best = [0, 0]
    best_score = -10**18

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            nx, ny = x, y
        # Main objective: be on/near a resource; secondary: stay away from opponent to deny races.
        if (nx, ny) in resset:
            score = 10**6
        else:
            score = -nearest_res_dist(nx, ny) * 1000
        score += manh(nx, ny, ox, oy) * 5

        # If resources are scarce, drift to center to improve future reach.
        if not reslist:
            score += -manh(nx, ny, center_x, center_y)

        # Deterministic tie-break: smallest dx, then dy (after score).
        if score > best_score or (score == best_score and (dx0, dy0) < (best[0], best[1])):
            best_score = score
            best = [dx0 if inb(x + dx0, y + dy0) else 0, dy0 if inb(x + dx0, y + dy0) else 0]

    # Ensure dx/dy are in {-1,0,1}
    dx, dy = best[0], best[1]
    if dx not in (-1, 0, 1):
        dx = 0
    if dy not in (-1, 0, 1):
        dy = 0
    return [dx, dy]