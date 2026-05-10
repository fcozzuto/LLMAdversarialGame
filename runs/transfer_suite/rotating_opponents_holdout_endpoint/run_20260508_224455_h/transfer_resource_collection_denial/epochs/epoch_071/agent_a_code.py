def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(int(p[0]), int(p[1])) for p in obs_list}

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target that we can reach significantly sooner than the opponent.
    best_targets = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        race = od - sd
        best_targets.append((race, -sd, rx, ry))
    best_targets.sort(reverse=True)
    # If race is small/negative, still move toward best "race" deterministically.
    rx, ry = best_targets[0][2], best_targets[0][3]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer: increase race margin; then decrease distance to target.
        val = (od - sd2) * 1000 - sd2
        # Mildly discourage stepping away in raw grid terms.
        val -= (abs(nx - sx) + abs(ny - sy)) * 0.01
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0) and (sx, sy) in obstacles:
        # Shouldn't happen, but keep safe.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]