def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    sp = observation.get("self_path") or []
    last = tuple(sp[-1]) if sp else None

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Deterministic target selection: prefer unclaimed far from opponent and not too far from us.
    best_target = None
    best_tscore = -10**18
    unclaimed_sorted = sorted(unclaimed)
    for i, (tx, ty) in enumerate(unclaimed_sorted[:24] if len(unclaimed_sorted) > 24 else unclaimed_sorted):
        tscore = (dist(tx, ty, ox, oy) - dist(tx, ty, x, y))
        # Mildly prefer cells aligned with our corner direction (stabilizes behavior)
        tscore += (tx + ty) * 0.01 if (x == 0 and y == 0) else 0
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (tx, ty)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        status_bonus = 0
        if (nx, ny) in unclaimed:
            status_bonus = 70
        elif (nx, ny) in oppT:
            # Stepping into opponent territory can flip; reward but don't overcommit.
            status_bonus = 45
        elif (nx, ny) in selfT:
            status_bonus = 15
        else:
            status_bonus = 5

        # Focus on reaching the chosen target.
        d_to_target = dist(nx, ny, tx, ty)
        d_from_opp = dist(nx, ny, ox, oy)

        val = status_bonus
        val += (d_from_opp * 0.8)  # keep distance from opponent while expanding
        val += (-2.0 * d_to_target)  # closer to target is better

        # Avoid loops: slight penalty for revisiting last position.
        if last is not None and (nx, ny) == last:
            val -= 6

        # Encourage progress: prefer moves that reduce distance to target compared to staying.
        val += (dist(x, y, tx, ty) - d_to_target) * 4.0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]