def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    myx, myy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def md(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy) ** 0.5

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -1e18

    # Precompute distances from current to resources for small decision stability
    opp_to = []
    for rx, ry in resources:
        opp_to.append(md(ox, oy, rx, ry))

    for dx, dy in moves:
        nx, ny = myx + dx, myy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue

        # Heuristic: maximize contested-resource advantage; also prefer being closer overall.
        score = 0.0
        if resources:
            local_best = -1e18
            for i, (rx, ry) in enumerate(resources):
                myd = md(nx, ny, rx, ry)
                oppd = opp_to[i]
                adv = oppd - myd
                # Encourage taking a resource if we are closer; discourage chasing when opponent is much closer.
                cand = adv * 3.0 - myd
                if cand > local_best:
                    local_best = cand
            score = local_best
        else:
            # No visible resources: drift to center.
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            score = -((nx - cx) ** 2 + (ny - cy) ** 2)

        # Tactical: if adjacent to opponent, move to increase distance slightly.
        dopp = md(nx, ny, ox, oy)
        score += dopp * 0.25

        # Deterministic tie-break: prefer earlier move order implicitly by strict >.
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best