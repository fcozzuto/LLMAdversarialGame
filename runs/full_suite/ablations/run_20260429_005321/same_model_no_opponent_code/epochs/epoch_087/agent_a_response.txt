def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp_pos(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    if not resources:
        # No visible resources: move to reduce distance to opponent corner-cross (deterministic)
        tx, ty = (w - 1 - sx), (h - 1 - sy)
    else:
        # Pick resource to maximize our advantage in race
        best = None
        best_key = None
        for r in sorted(resources):
            ourd = man((sx, sy), r)
            oppd = man((ox, oy), r)
            # Prefer resources where we are closer; tie-break deterministically
            key = (oppd - ourd, -ourd, -r[0], -r[1])
            if best is None or key > best_key:
                best = r
                best_key = key
        tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = clamp_pos(sx + dx, sy + dy)
            # Do not allow moving into obstacles: heavy penalty instead of relying on engine
            into_obs = (nx, ny) in obstacles
            our_after = man((nx, ny), (tx, ty))
            opp_after = man((ox, oy), (tx, ty))  # opponent not moved this turn
            # Move desirability: gain in race and approach target
            gain = opp_after - our_after
            # Prefer reducing our distance and avoid into-obstacle and prefer non-still if equally good
            cand_key = (gain, -our_after, -abs(nx - tx) - abs(ny - ty), -into_obs, -int(dx == 0 and dy == 0), -dx, -dy)
            candidates.append((cand_key, [dx, dy]))

    candidates.sort(reverse=True, key=lambda t: t[0])
    return candidates[0][1]