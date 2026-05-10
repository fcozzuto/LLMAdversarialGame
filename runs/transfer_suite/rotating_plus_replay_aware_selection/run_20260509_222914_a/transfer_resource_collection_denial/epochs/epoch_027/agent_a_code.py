def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))
    resset = set(res)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, (nx,ny))
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue

        # Immediate pickup advantage
        if (nx, ny) in resset:
            score = -100000 - (md(nx, ny, ox, oy))
        elif not res:
            # If no visible resources: drift toward center while not walking into opponent vicinity
            cx, cy = w // 2, h // 2
            score = md(nx, ny, cx, cy) + 0.3 * md(nx, ny, ox, oy)
        else:
            # Choose state that improves our advantage to the closest contested resource
            # Objective: minimize (our distance - opp distance), plus a small tie-break on our distance
            score = None
            for rx, ry in res:
                dme = md(nx, ny, rx, ry)
                dpo = md(ox, oy, rx, ry)
                if score is None:
                    score = dme - dpo + 0.01 * dme
                else:
                    cand = dme - dpo + 0.01 * dme
                    if cand < score:
                        score = cand

        key = (score, (nx, ny))
        if best is None or key < best:
            best = key

    if best is None:
        return [0, 0]
    return [best[1][0] - x, best[1][1] - y]