def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "")
    pursuer = ("pursuer" in role.lower()) or ("catch" in role.lower()) or ("hunter" in role.lower())
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def corner_score(x, y):
        # Higher means more "cornered"
        return (1 if x in (0, w - 1) else 0) + (1 if y in (0, h - 1) else 0)

    opp_cornered = corner_score(ox, oy)
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny)
        # Tie-break logic varies by role
        if pursuer:
            # Primary: minimize distance; secondary: if opponent cornered, also avoid drifting away from that corner.
            target_bonus = 0
            if opp_cornered:
                # Encourage moving toward opponent along the axes where they are cornered.
                target_bonus = (1 if (ox == 0 and nx <= sx) or (ox == w - 1 and nx >= sx) else 0) + (1 if (oy == 0 and ny <= sy) or (oy == h - 1 and ny >= sy) else 0)
            val = (-d, -(target_bonus), corner_score(nx, ny))  # corner_score lower is better for pursuer
        else:
            # Evader: maximize distance; avoid becoming too cornered; also prefer moving toward center if possible.
            center_x = (w - 1) / 2.0
            center_y = (h - 1) / 2.0
            center_d = (nx - center_x) * (nx - center_x) + (ny - center_y) * (ny - center_y)
            val = (d, -(corner_score(nx, ny)), -(center_d))  # smaller corner_score and larger center_d better
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        # If all moves blocked (unlikely), try staying.
        return [0, 0]
    return best