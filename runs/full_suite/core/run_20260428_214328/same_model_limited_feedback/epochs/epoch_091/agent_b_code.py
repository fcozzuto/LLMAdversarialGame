def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    x, y = self_pos[0], self_pos[1]
    ox, oy = opp_pos[0], opp_pos[1]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_moves = []

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for diagonal moves

    # Pick a target resource that I'm competitive for; otherwise switch to opponent pressure
    best_target = None
    best_val = None
    for r in resources:
        rx, ry = r[0], r[1]
        myd = dist((x, y), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        if myd <= opd:
            val = myd - 0.75 * opd  # smaller is better
        else:
            val = myd - 0.25 * opd + 3.0  # discourage resources opponent is closer to
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)

    favorable = False
    if best_target is not None:
        rt = best_target
        favorable = dist((x, y), rt) <= dist((ox, oy), rt)

    def cand_score(nx, ny):
        if favorable and best_target is not None:
            rt = best_target
            base = dist((nx, ny), rt)
            # Add blocking pressure: if opponent is closer to the target, prefer reducing their approach
            opp_base = dist((ox, oy), rt)
            myd = dist((nx, ny), rt)
            block = 0.35 * (myd - opp_base)
            return base + block
        # No favorable resource: chase opponent to reduce their efficiency
        return dist((nx, ny), (ox, oy)) + 0.2 * dist((nx, ny), best_target) if best_target is not None else dist((nx, ny), (ox, oy))

    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        sc = cand_score(nx, ny)
        if best_score is None or sc < best_score:
            best_score = sc
            best_moves = [(dx, dy)]
        elif sc == best_score:
            best_moves.append((dx, dy))

    # Deterministic tie-break: prefer moves that also do not move away from chosen goal/opponent
    if not best_moves:
        return [0, 0]
    goal = best_target if (favorable and best_target is not None) else (ox, oy)
    best_dir = None
    best_d = None
    for dx, dy in best_moves:
        nx, ny = x + dx, y + dy
        d = dist((nx, ny), goal)
        if best_d is None or d < best_d:
            best_d = d
            best_dir = [dx, dy]
    return best_dir