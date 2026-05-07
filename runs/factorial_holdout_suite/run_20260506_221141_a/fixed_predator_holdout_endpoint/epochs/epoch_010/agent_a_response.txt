def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    if not resources:
        return [0, 0]

    obst = {(int(a), int(b)) for a, b in obstacles}

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_key = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        best_adv = None
        best_selfd = None
        opp_better_count = 0

        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd
            if od <= sd:
                opp_better_count += 1

        # Prefer steps that create the biggest lead on some resource,
        # while limiting how many resources the opponent is not worse on.
        key = (-best_adv, best_selfd, opp_better_count, md(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]