def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = obstacles  # local alias

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    # If no resources, just move to maximize distance from opponent while avoiding obstacles
    if not resources:
        best = None
        bestv = -1e18
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            dv = dist((nx, ny), (ox, oy))
            if dv > bestv:
                bestv = dv
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    best_move = (0, 0)
    best_val = -1e18

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue

        # Select a resource where we are relatively closer than opponent; prioritize hard grabs.
        # Advantage = (our_dist - opp_dist). Lower is better; convert to higher score.
        best_adv = 1e18
        for rx, ry in resources:
            ad = ((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)) ** 0.5
            bd = ((ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)) ** 0.5
            adv = ad - 0.85 * bd
            if adv < best_adv:
                best_adv = adv

        # Also encourage safety: don't drift too close to opponent while going for a grab.
        safety = dist((nx, ny), (ox, oy))
        # Encourage not staying still if we're not already on a resource.
        on_resource = any(nx == rx and ny == ry for rx, ry in resources)
        still_pen = -0.2 if not on_resource and dx == 0 and dy == 0 else 0.0

        val = (-2.4 * best_adv) + (0.35 * safety) + still_pen

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]