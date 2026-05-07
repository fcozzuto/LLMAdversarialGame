def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]

    def in_bounds(nx, ny):
        return 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]

    def best_target():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            d = abs(rx - x) + abs(ry - y)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is None:
            # all resources blocked: pick any unblocked-ish move
            return None
        return best[1]

    target = best_target()
    if target is None:
        # fallback: move away from obstacles if possible, else toward opponent
        candidates = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny) or (nx, ny) in obs:
                    continue
                dist_opp = abs(ox - nx) + abs(oy - ny)
                # prefer closer to opponent deterministically, but avoid obstacles already
                candidates.append((dist_opp, dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort()
        return [candidates[0][1], candidates[0][2]]

    rx, ry = target

    # greedy step toward target with deterministic tie-break; avoid obstacles
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx or dy):
                continue
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            # primary: reduce distance to target; secondary: deterministic by dx,dy
            newd = abs(rx - nx) + abs(ry - ny)
            options.append((newd, abs(rx - nx), abs(ry - ny), dx, dy))
    if options:
        options.sort()
        return [options[0][3], options[0][4]]

    # if blocked in greedy direction, try any legal move (including diagonals), else stay
    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                # prefer staying still only if it's the only legal move
                if dx == 0 and dy == 0:
                    legal.append((1e9, 0, 0))
                else:
                    newd = abs(rx - nx) + abs(ry - ny)
                    legal.append((newd, dx, dy))
    if not legal:
        return [0, 0]
    legal.sort()
    if legal[0][1] == 0 and legal[0][2] == 0 and len(legal) > 1:
        # find first non-stay move
        for a in legal:
            if a[1] != 0 or a[2] != 0:
                return [a[1], a[2]]
    return [legal[0][1], legal[0][2]]