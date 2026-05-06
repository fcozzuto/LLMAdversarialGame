def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def move_score(nx, ny):
        best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Primary: maximize ability to out-approach compared to opponent
            adv = oppd - selfd  # positive is good

            # Secondary: if opponent is currently ahead on this resource, strongly prioritize catching up
            catch = 0
            if oppd < selfd:
                catch = (selfd - oppd) * 3  # bigger gap => bigger urgency to reduce it

            # Tertiary: shorter self distance among similarly contested resources
            local = adv * 10 + (oppd * 0.2) - selfd - catch

            # Small bias to reduce opponent's "chasing" by steering to resources that are closer to self than opponent
            if adv <= 0:
                local -= (1 - adv) * 2

            if local > best:
                best = local
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        val = move_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move