def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if W <= 0 or H <= 0:
        return [0, 0]

    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs_set.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Drift toward center to reduce corner disadvantage
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = -10**18
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            score = -man(nx, ny, tx, ty)
            if score > best:
                best = score
                best_move = [dx, dy]
        return best_move

    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # Huge bonus for stepping onto a resource this turn
        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 10**9
                break

        if immediate:
            score = immediate - 0.1 * man(nx, ny, ox, oy)
        else:
            # Choose move that maximizes advantage: opponent farther than us to the same resource
            score = -10**18
            for rx, ry in resources:
                d_me = man(nx, ny, rx, ry)
                d_opp = man(ox, oy, rx, ry)
                # Prefer resources where we arrive sooner (or at least contest well)
                advantage = d_opp - d_me
                # Penalize being far; slightly reward being closer to multiple winning chances by taking max
                s = advantage * 100 - d_me
                if s > score:
                    score = s

        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move