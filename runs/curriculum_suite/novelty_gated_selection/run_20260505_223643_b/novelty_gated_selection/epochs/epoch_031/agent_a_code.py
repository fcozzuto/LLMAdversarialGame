def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_dxdy = (0, 0)
    best_key = None

    # Deterministic target: either secure a resource we can reach earlier,
    # or otherwise push to reduce our "threat" by increasing the opponent's nearest resource distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        diffs = []
        opp_near = 10**9
        my_near = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if do < opp_near: opp_near = do
            if ds < my_near: my_near = ds
            diffs.append((do - ds, ds, do, rx, ry))  # advantage for us

        best_adv = -10**9
        best_ds = 10**9
        best_do = 10**9
        for adv, ds, do, rx, ry in diffs:
            if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and do < best_do))):
                best_adv, best_ds, best_do = adv, ds, do

        # If we can secure at least one resource earlier (adv>0), prioritize that.
        # Otherwise, act as an "anti-nearest" move: maximize opponent's nearest-resource distance after we reposition.
        if best_adv > 0:
            # Prefer larger advantage, then faster pick, then farther from opponent (less contest).
            key = (0, -best_adv, best_ds, -man(nx, ny, ox, oy))
        else:
            # We can't beat the opponent to any resource this step: still avoid losing tempo.
            # Use our move to maximize opponent's remaining nearest resource distance "gap".
            # Gap: (opponent_nearest - our_nearest) is good for us being able to contest later.
            # Also break ties by moving closer to the opponent (to intercept) or stay safe if equal.
            gap = opp_near - my_near
            # Secondary: choose move that makes the most advantaged resource for us as large as possible (even if <=0).
            max_adv = best_adv  # <=0
            key = (1, -gap, -max_adv, man(nx, ny, ox, oy))

        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]