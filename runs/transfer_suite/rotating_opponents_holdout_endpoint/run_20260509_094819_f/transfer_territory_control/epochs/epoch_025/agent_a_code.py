def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(v):
        out = set()
        if not v:
            return out
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                out.add((x, y))
        return out

    obstacles = to_set(observation.get("obstacles") or [])
    unclaimed = to_set(observation.get("unclaimed_cells") or [])
    selfT = to_set(observation.get("self_territory") or [])
    oppT = to_set(observation.get("opponent_territory") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def adj_to_self(x, y):
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in selfT:
                return True
        return False

    def adj_to_opp(x, y):
        return max(abs(x - ox), abs(y - oy)) <= 1

    # Prefer expanding into unclaimed and stealing nearby opponent cells while advancing toward opponent.
    best = -10**18
    best_move = [0, 0]
    # Tie-break deterministically by fixed move order
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_score = 0
        if (nx, ny) in unclaimed:
            cell_score += 6
        elif (nx, ny) in oppT:
            cell_score += 10  # attempt to steal/flip
            if adj_to_opp(nx, ny):
                cell_score -= 3  # likely contested
        else:
            cell_score += 1 if (nx, ny) in selfT else 0

        # Expand outward: adjacent to our territory is safer and usually increases reach.
        if adj_to_self(nx, ny):
            cell_score += 3

        # Advance toward opponent.
        cell_score += -dist2(nx, ny, ox, oy) / 8.0

        # Discourage getting boxed by obstacles (local penalty).
        local_obs = 0
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                local_obs += 1
        cell_score -= 0.6 * local_obs

        if cell_score > best:
            best = cell_score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]